#!/usr/bin/env python3
"""
Test Vietnamese text processing with vi-stag library
"""

def test_vi_stag_processing():
    """Test Vietnamese text processing with vi-stag"""
    
    print("🇻🇳 Testing Vietnamese Text Processing with vi-stag")
    print("=" * 60)
    
    # Vietnamese test sentences
    test_sentences = [
        "Xin chào, tôi là trợ lý AI cho game PokeMMO",
        "Làm thế nào để tải game PokeMMO trên điện thoại?",
        "Hướng dẫn hoàn thành cốt truyện Pokemon Fire Red",
        "Cách kiếm tiền hiệu quả trong PokeMMO",
        "Xây dựng đội hình PvP mạnh nhất"
    ]
    
    try:
        # Try to import vi-stag
        from vi_stag import ViStag
        print("✅ vi-stag library found")
        
        # Initialize ViStag
        vi_stag = ViStag()
        print("✅ ViStag initialized successfully")
        
        for i, text in enumerate(test_sentences, 1):
            print(f"\n{i}. Processing: {text}")
            print("-" * 50)
            
            try:
                # Tokenize
                print("   🔤 Tokenization:")
                tokens = vi_stag.tokenize(text)
                print(f"      Tokens: {tokens}")
                
                # POS tagging
                print("   📝 POS Tagging:")
                pos_tags = vi_stag.pos_tag(text)
                print(f"      POS Tags: {pos_tags}")
                
                # Named Entity Recognition
                print("   🏷️  Named Entity Recognition:")
                entities = vi_stag.ner(text)
                print(f"      Entities: {entities}")
                
                # Dependency parsing (if available)
                try:
                    print("   🌳 Dependency Parsing:")
                    dependencies = vi_stag.dependency_parse(text)
                    print(f"      Dependencies: {dependencies}")
                except Exception as e:
                    print(f"      ⚠️  Dependency parsing not available: {e}")
                
                # Sentiment analysis (if available)
                try:
                    print("   😊 Sentiment Analysis:")
                    sentiment = vi_stag.sentiment(text)
                    print(f"      Sentiment: {sentiment}")
                except Exception as e:
                    print(f"      ⚠️  Sentiment analysis not available: {e}")
                
            except Exception as e:
                print(f"   ❌ Processing failed: {e}")
                
    except ImportError:
        print("❌ vi-stag library not found")
        print("   Install with:")
        print("   pip install vi-stag")
        print("   or")
        print("   conda install -c conda-forge vi-stag")
        return False
    except Exception as e:
        print(f"❌ vi-stag initialization failed: {e}")
        return False
    
    print("\n🎉 vi-stag processing test completed!")
    return True

def test_underthesea_processing():
    """Test Vietnamese text processing with underthesea library"""
    
    print("\n🇻🇳 Testing Vietnamese Text Processing with underthesea")
    print("=" * 60)
    
    test_sentences = [
        "Xin chào, tôi là trợ lý AI cho game PokeMMO",
        "Làm thế nào để tải game PokeMMO trên điện thoại?",
        "Hướng dẫn hoàn thành cốt truyện Pokemon Fire Red"
    ]
    
    try:
        # Try to import underthesea
        from underthesea import word_tokenize, pos_tag, ner, sentiment
        print("✅ underthesea library found")
        
        for i, text in enumerate(test_sentences, 1):
            print(f"\n{i}. Processing: {text}")
            print("-" * 50)
            
            try:
                # Word tokenization
                print("   🔤 Word Tokenization:")
                tokens = word_tokenize(text)
                print(f"      Tokens: {tokens}")
                
                # POS tagging
                print("   📝 POS Tagging:")
                pos_tags = pos_tag(text)
                print(f"      POS Tags: {pos_tags}")
                
                # Named Entity Recognition
                print("   🏷️  Named Entity Recognition:")
                entities = ner(text)
                print(f"      Entities: {entities}")
                
                # Sentiment analysis
                print("   😊 Sentiment Analysis:")
                sentiment_result = sentiment(text)
                print(f"      Sentiment: {sentiment_result}")
                
            except Exception as e:
                print(f"   ❌ Processing failed: {e}")
                
    except ImportError:
        print("❌ underthesea library not found")
        print("   Install with: pip install underthesea")
        return False
    except Exception as e:
        print(f"❌ underthesea processing failed: {e}")
        return False
    
    print("\n🎉 underthesea processing test completed!")
    return True

if __name__ == "__main__":
    print("🚀 Vietnamese Text Processing Libraries Test")
    print("=" * 60)
    
    # Test vi-stag
    vi_stag_success = test_vi_stag_processing()
    
    # Test underthesea
    underthesea_success = test_underthesea_processing()
    
    print("\n📋 Summary:")
    print(f"   vi-stag: {'✅ Success' if vi_stag_success else '❌ Failed'}")
    print(f"   underthesea: {'✅ Success' if underthesea_success else '❌ Failed'}")
    
    if vi_stag_success or underthesea_success:
        print("\n🎉 At least one Vietnamese processing library is working!")
    else:
        print("\n⚠️  No Vietnamese processing libraries are working.")
        print("   Install libraries with:")
        print("   pip install vi-stag underthesea")
